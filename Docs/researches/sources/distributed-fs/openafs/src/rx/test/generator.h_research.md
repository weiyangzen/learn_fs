# sources/distributed-fs/openafs/src/rx/test/generator.h

## Purpose
`generator.h` defines the constants, utility macros, and data structures shared by `generator.c` for RX generated-test creation.

## Important APIs, Types, and Functions
- `arg_tuple` describes one RPC argument: direction, type, optional attributes, generated input/output value strings, and array bounds.
- `rpcArgs` wraps an argument count and a dynamically allocated `arg_tuple` vector.
- Constants such as `TESTS_PER_FILE`, `IDL_STR_MAX`, `IDL_FIX_ARRAY_SIZE`, `MAX_SERV_NAME`, and string-length limits drive both parser assumptions and generated code shape.
- `MEM_CHK`, `FATAL`, `PrintShortUsage`, and `PrintLongUsage` centralize fail-fast behavior and CLI help text.

## Control Flow
This header has no runtime control flow, but its constants control `generator.c` batching, allocation sizes, and generated IDL dimensions.

## State and Persistence
The header defines only compile-time state. The value pointer arrays in `arg_tuple` imply ownership by `generator.c`, which allocates and frees generated strings per signature.

## Dependencies and Integration Points
Included directly by `generator.c`; its schema must match `tableGen.c` output vocabulary (`IN`, `OUT`, `INOUT`, scalar and array type names) and generated rxgen type names.

## Risks and Edge Cases
Many field sizes are hard-coded. New direction/type strings must fit `MAX_DIR_STR` and `MAX_TYP_STR`; otherwise `fscanf("%s")` in `generator.c` can overflow. `IDL_FIX_ARRAY_SIZE` and array value pointer counts must remain aligned.

## Test Signals
Compile success of `generator.c` and successful generation/parsing of all table signatures are the main signals. Mismatched constants show up as malformed generated `.xg` or C output.
