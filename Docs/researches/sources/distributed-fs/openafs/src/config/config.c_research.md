# sources/distributed-fs/openafs/src/config/config.c

Purpose: command-line driver for generating platform-specific makefiles from prototype files.

Important APIs/types/functions: `main` validates `config <from file> <to file> <system name>`, opens input/output files, constructs an option list containing the full sysname, `all`, and split architecture/OS-version tokens, then calls `mc_copy(FILE *, FILE *, char **)`.

Control flow: after file setup, the sysname is duplicated and split on the first underscore so a platform such as `amd64_linux26` can match full-name, architecture-only, or OS-version-only sections in a Makefile prototype. `mc_copy` performs the conditional copy; errors print diagnostics and exit nonzero.

State and persistence: writes the generated output makefile. It includes `AFS_component_version_number.c`, embedding build version state into the tool binary.

Dependencies and integration: built by `src/config/Makefile.in` with `mc.o`; used for kernel/libafs MakefileProto conversion where conditional sections are tagged by sysname tokens.

Risks and test signals: risks include output truncation only through libc errors, leaked duplicated sysname on exit, and simplistic first-underscore splitting. Signals are generated Makefiles for full sysname, architecture-only, OS-only, and `all` sections, plus failure behavior for missing files.
