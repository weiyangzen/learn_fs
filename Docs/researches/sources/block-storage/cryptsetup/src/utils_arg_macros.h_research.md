# File Research: sources/block-storage/cryptsetup/src/utils_arg_macros.h

## Purpose
Typed accessor and setter macros for `tool_core_args[]`.

## Accessors
- `ARG_SET(id)` checks whether an option was supplied.
- `ARG_STR`, `ARG_INT32`, `ARG_UINT32`, `ARG_INT64`, and `ARG_UINT64` assert the expected stored type and return the value.

## Setters
- `ARG_SET_TRUE` marks a boolean option as set.
- `ARG_SET_STR`, `ARG_SET_INT32`, `ARG_SET_UINT32`, `ARG_SET_INT64`, and `ARG_SET_UINT64` assert that the option was previously unset and of the expected type, then store the value and mark it set.
- String setter takes ownership of the supplied allocated string.

## Alias Initialization
`ARG_INIT_ALIAS(id)` resolves a `CRYPT_ARG_ALIAS` entry by storing a pointer to the canonical `tools_arg` target.

## Notes
These macros are GNU C statement expressions for getters, not standard C expressions. They rely on a visible `tool_core_args` symbol in each CLI translation unit.
