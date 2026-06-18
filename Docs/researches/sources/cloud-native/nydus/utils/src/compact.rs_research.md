# sources/cloud-native/nydus/utils/src/compact.rs

Purpose: wraps platform-specific device number encoding/decoding so Linux and macOS callers can use common helpers.

Important APIs/types/functions: `makedev(major, minor)`, `major_dev(dev)`, and `minor_dev(dev)`. Linux delegates to `nix::sys::stat`; macOS uses bit operations compatible with xnu device encoding.

Control flow: compile-time cfg selects Linux or macOS implementations.

State and persistence: none.

Dependencies and integration points: depends on `nix::sys::stat::dev_t`. Used where filesystem metadata/device ids must be constructed or decoded portably.

Risks: macOS bit expressions rely on operator precedence; the current expression `major & 0xff << 24` should be read carefully because shift precedence can be surprising. Linux tests do not validate macOS behavior. Large values are masked by platform encodings.

Test signals: Linux-only tests cover round-tripping normal and large major/minor values and direct nix compatibility.
