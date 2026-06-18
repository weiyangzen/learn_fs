# sources/compression/xz/windows/build.bash

Purpose: packaging script for XZ Utils Windows binary distributions using the GNU Autotools build system and MinGW-w64/MSYS toolchains.

Important APIs/functions: shell functions `buildit` and `txtcp`. `buildit` runs two configure/build cycles per architecture: a size-optimized static tool set and a normal speed-optimized `xz.exe` plus `liblzma.dll`. `txtcp` copies text files while converting LF to CRLF.

Control flow: validates working directory and required MinGW runtime license file, derives make job count, detects native MSYS builds for optional `make check`, builds i686 SSE2 and x86-64 variants if compilers are in `PATH`, optionally builds PDFs, copies headers/docs/examples into `pkg`, then uses 7-Zip if found to create `.zip` and `.7z` packages.

State and persistence: mutates the source/build tree with `make distclean`, creates `pkg/`, copies binaries/docs, strips outputs, and optionally creates `xz-<version>-windows.zip` and `.7z` at the package root.

Dependencies and integration: requires generated distribution files from `make mydist`, Autotools, MinGW-w64 GCC triplets, make, optional `ps2pdf`, optional 7-Zip, and `windows/COPYING.MinGW-w64-runtime.txt`.

Risks: `set -e` aborts on any failed command; repeated `distclean` means it should be run only in a disposable distribution tree. Whitespace detection in the current directory is conservative. If triplet-specific `windres`/`strip` are missing, it prepends the GCC directory to `PATH` to avoid mixing toolchains.

Test signals: native MSYS builds run `make check` or `make -C tests check`; cross-compilation skips runtime tests. The script ends with a success message only after packaging steps complete or optional archive creation is skipped.
