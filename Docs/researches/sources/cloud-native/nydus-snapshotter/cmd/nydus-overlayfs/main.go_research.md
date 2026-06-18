# sources/cloud-native/nydus-snapshotter/cmd/nydus-overlayfs/main.go

Purpose: mount helper that filters Nydus/Kata-specific overlay options before invoking kernel overlayfs.

Flow: CLI expects `overlay <target> -o <options>`. `parseArgs` validates fs type/target and strips `extraoption=` and Kata volume options. `parseOptions` maps known mount option strings to flags and leaves overlay data options. If data nears page size, `compactLowerdirOption` computes a common directory, chdirs there, and rewrites lower/upper/work dirs relative before `syscall.Mount`.

State/dependencies: changes current working directory before mount when compacting; uses Unix mount flags.

Integration points: enabled by snapshotter config for containerd mount helper flow.

Risks/tests: mount option flag table maps some positive options to negating flags (`rw` to `MS_RDONLY`, etc.), matching legacy patterns but risky. Tests cover parsing and compaction, not actual mount syscall.
