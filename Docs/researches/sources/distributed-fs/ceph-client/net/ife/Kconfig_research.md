# sources/distributed-fs/ceph-client/net/ife/Kconfig

## Purpose
`net/ife/Kconfig` adds the configuration switch for Inter-FE encapsulation support.

## Important APIs, types, and functions
The single symbol is `NET_IFE`, a tristate `menuconfig` titled `Inter-FE based on IETF ForCES InterFE LFB`, defaulting to `n`.

## Control flow
Kconfig selection controls whether `ife.o` is built in, built as a module, or omitted. Choosing module mode names the module `ife`.

## State and persistence
The persistent result is the generated kernel configuration value for `CONFIG_NET_IFE`; no runtime state is represented here.

## Dependencies and integration points
The symbol is consumed by `net/ife/Makefile`. The help text points to the InterFE LFB design and the traffic-control classifier/action distribution use case.

## Risks and invariants
Because the symbol has no explicit dependencies, the implementation must compile wherever the surrounding networking stack supports it. Changing the symbol name would break Makefile wiring and downstream configs.

## Test signals
Configuration tests should verify `CONFIG_NET_IFE=y` links `ife.o`, `CONFIG_NET_IFE=m` builds `ife.ko`, and `CONFIG_NET_IFE=n` omits the object.
