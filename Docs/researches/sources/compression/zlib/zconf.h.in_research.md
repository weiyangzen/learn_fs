# sources/compression/zlib/zconf.h.in

`zconf.h.in` is the template used to generate `zconf.h`. It carries the same public configuration surface while allowing configure/CMake substitution for prefixing and platform feature probes.

The template covers symbol remapping, platform normalization, standard-C detection, `z_size_t`, memory/window defaults, old-style prototype support, far pointer and calling convention setup, public typedefs, CRC type selection, optional includes, large-file offset decisions, and MVS pragma mappings. Its persistent effect is the generated public `zconf.h`.

Integration points are configure/CMake/release tooling, installed headers, and every zlib translation unit. Risks are drift from checked-in `zconf.h`, broken substitution syntax, and incomplete updates when public/internal symbols are added. Test signals include regenerating `zconf.h` with expected differences only and building configured/non-configured, prefixed, solo, DLL, and large-file variants.
