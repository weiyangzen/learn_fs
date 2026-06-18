# sources/distributed-fs/ceph-client/drivers/of/module.c

## Purpose
`module.c` builds OF modalias strings and requests matching kernel modules for devicetree nodes. It supports module autoloading from node name, device type, and compatible strings.

## Important APIs, types, and functions
`of_modalias()` formats a modalias into a caller-provided buffer and returns the total length that would be required. `of_request_module()` allocates a correctly sized alias and calls `request_module()`.

## Control flow and state
`of_modalias()` validates buffer and length arguments, writes an `of:N<name>T<type>` prefix, then appends each compatible string with a `C` prefix. Spaces in compatible strings are normalized to underscores in the written buffer. It tracks total size separately from copied size so callers can detect truncation. `of_request_module()` first asks for size with a zero-length call, allocates one extra byte for NUL termination, emits the alias, requests the module, then frees the temporary string.

## Dependencies and integration
The file uses OF property string iteration, `%pOFn` formatting, module loader APIs, and is consumed by `device.c` for modalias uevents.

## Risks and test signals
Risks include negative lengths, NULL buffers with nonzero length, truncation, unexpected spaces in compatible strings, and unbounded module autoload behavior for malformed firmware strings. Test signals are modalias sysfs/uevent output and successful autoload of OF-matched drivers.
