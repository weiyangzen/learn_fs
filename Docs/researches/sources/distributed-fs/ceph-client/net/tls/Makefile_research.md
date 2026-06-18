# sources/distributed-fs/ceph-client/net/tls/Makefile

## Purpose
Builds the kTLS subsystem object set according to the selected kernel configuration.

## Important Build Rules
`obj-$(CONFIG_TLS) += tls.o` builds the aggregate TLS object. `tls-y` always includes `tls_main.o`, `tls_sw.o`, `tls_proc.o`, `trace.o`, and `tls_strp.o`. `tls-$(CONFIG_TLS_TOE)` adds `tls_toe.o`, and `tls-$(CONFIG_TLS_DEVICE)` adds `tls_device.o` plus `tls_device_fallback.o`. `CFLAGS_trace.o := -I$(src)` lets trace generation include local trace headers.

## Control Flow And State
There is no runtime state, but object composition controls which symbols are linked and which `tls.h` paths are live. Device offload support is all-or-nothing at build time for the implementation files, while runtime availability still depends on netdev features and driver `tlsdev_ops`.

## Dependencies And Integration Points
Integrates with kernel kbuild and the Kconfig options in the same directory. The aggregate `tls.o` is the module or built-in unit consumed by the networking stack.

## Risks And Test Signals
Risk is primarily build drift: adding APIs to `tls.h` without adding corresponding objects under the right config, or breaking trace include paths. Test signals include `CONFIG_TLS=m`, built-in TLS, TLS without device offload, TLS with TOE, and TLS with device offload builds.
