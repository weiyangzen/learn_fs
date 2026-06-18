# sources/distributed-fs/ceph/src/rgw/rgw_es_query.h

## Purpose
Declares the public surface for compiling RGW search expressions into Elasticsearch JSON: token stack, infix parser, entity type map, and compiler configuration.

## Important APIs, Types, And Functions
`ESQueryStack` wraps a `std::list<std::string>` with `peek()`, `pop()`, and `done()`. `ESInfixQueryParser` stores query text and exposes `parse()`. `ESEntityTypeMap` maps field names to `ES_ENTITY_STR`, `ES_ENTITY_INT`, or `ES_ENTITY_DATE`. `ESQueryCompiler` accepts a query, optional prepended equality conditions, and a custom metadata prefix; callers configure generic/custom type maps, field aliases, and restricted fields before calling `compile()` and `dump()`.

## Control Flow
The header establishes a two-phase API: configure compiler metadata, call `compile()` to produce a private `ESQueryNode` tree, then call `dump(Formatter*)` to serialize. Field aliasing and restricted checks are resolved during node initialization, not at parse time.

## State And Persistence Behavior
All state is transient. `ESQueryCompiler` owns `query_root`; parser and stack are embedded by value. `eq_conds` is moved from the caller-provided list, which is important for call-site ownership expectations.

## Dependencies And Integration Points
Depends on `rgw_string.h` for `ltstr_nocase`, standard containers, and `Formatter` via implementation includes. It is consumed by RGW services that expose metadata search over Elasticsearch.

## Risks
The API uses raw pointers for maps/sets and the query root, so callers must keep configured maps alive through compilation. `is_restricted()` checks exact set membership after aliasing. `ESQueryStack::assign()` swaps away the caller's list contents, which is efficient but destructive.

## Test Signals
Header-level tests should instantiate a compiler with aliases, type maps, restricted fields, and prepended equality conditions, then verify `compile()` behavior and emitted JSON through a formatter.
