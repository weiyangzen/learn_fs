<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/features/Features.hh -->
# sources/distributed-fs/eos/mgm/features/Features.hh

## Purpose

`Features.hh` declares the minimal MGM `Features` class, which acts as a namespace for a static map of feature-name to feature-value strings.

## Important APIs, Types, and Functions

The only public member is `static const std::map<const std::string, const std::string> sMap`. The keys and values are defined in `Features.cc`.

## Control Flow

There is no executable control flow in the header. Consumers include the header and read `Features::sMap`; initialization happens in the `.cc`.

## State and Persistence Behavior

The header declares process-global immutable state owned by the implementation. There is no persistence, mutation API, or synchronization requirement because the map is const after initialization.

## Dependencies and Integration Points

It depends on MGM namespace macros plus `<string>` and `<map>`. It integrates with MGM components that advertise capabilities to clients or administrative commands.

## Risks and Edge Cases

Because the map is a static object, ABI and initialization behavior depend on exactly one linked definition. The type uses `const std::string` as the key type; this works for a read-only map but is unusual and could complicate generic code expecting `std::map<std::string, std::string>`.

## Test Signals

Header self-containment compile tests and feature-advertisement integration tests are enough. Tests should verify known keys are present and values match the implementation under controlled environment.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/features/Features.hh -->
