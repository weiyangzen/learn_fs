# sources/distributed-fs/ceph-client/arch/arm64/kernel/pi/Makefile

Purpose: Builds the position-independent early arm64 startup objects that run before full kernel relocation and normal runtime services are available.

Important rules and state: `KBUILD_CFLAGS` removes ftrace, stack protector, SCS, LTO, fortify, branch profiling, latent entropy, and unwind table assumptions, then adds `-fpie`, `-ffreestanding`, hidden include, libfdt include path, and strict no-exports behavior. `CFLAGS_map_range.o += -mstrict-align` protects MMU-off execution. The `%.pi.o` rule prefixes symbols with `__pi_`, strips `.note.gnu.property`, and runs `relacheck`.

Control flow: object list always includes `idreg-override`, `map_kernel`, `map_range`, and selected libfdt objects. Relocatable, KASLR, and dynamic SCS patching add optional PI objects. Library source files are compiled from `lib/*.c` and object-copied so allocated sections become init sections when needed.

Dependencies and integration: consumed by `head.S` and linker aliases in `image-vars.h`. Depends on objcopy, a host `relacheck` tool, libfdt sources, and early startup constraints forbidding absolute addressing.

Risks and test signals: risks are compiler flags reintroducing instrumentation, relocations unsafe for early PI code, unaligned accesses with MMU off, and missing symbol prefixing. Test with `relacheck`, `readelf -r` on PI objects, KASLR/relocatable builds, LTO/SCS configurations, and early boot smoke.
