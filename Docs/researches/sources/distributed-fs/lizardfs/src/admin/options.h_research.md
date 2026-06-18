<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/options.h -->
# sources/distributed-fs/lizardfs/src/admin/options.h

## Purpose
Declares the `Options` parser/result object used by admin commands.

## Important APIs, Types, and Functions
Defines nested `ParseError`, constructor, `arguments`, `argument`, `isSet`, `getValue<T>`, `isOptionExpected`, `isOptionValued`, private `convert<T>`, and explicit specializations for string and numeric types.

## Control Flow, State, and Persistence
The object owns `options_`, `valued_options_`, and positional `arguments_`. `isSet` asserts the option was expected; `getValue` returns the default when not set or converts the stored string using the appropriate `std::sto*` function.

## Dependencies and Integration Points
Depends on project exception macros and common assertions. It is consumed by every `LizardFsProbeCommand::run` implementation.

## Risks and Test Signals
Risks include unchecked `argument(pos)` indexing, conversion exceptions not wrapped as `ParseError`, no bool/custom conversions, and assertions disappearing in release builds. Unit tests should cover typed conversions, defaults, invalid numeric strings, and out-of-range values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/options.h -->
