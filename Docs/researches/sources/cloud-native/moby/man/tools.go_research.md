<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/man/tools.go -->
# sources/cloud-native/moby/man/tools.go

Purpose: Go tools file that pins the `go-md2man/v2` dependency for manpage generation. It imports the tool for side effects under package `man`, ensuring module-aware tooling retains it. Control flow and runtime state are absent. Dependencies are build/toolchain module resolution. Risks are low; deleting this file could drop the manpage generator from module dependencies. Test signal is build dependency reproducibility.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/man/tools.go -->
