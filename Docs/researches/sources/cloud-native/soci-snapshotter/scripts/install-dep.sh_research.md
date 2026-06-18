# sources/cloud-native/soci-snapshotter/scripts/install-dep.sh

Purpose: installs native build dependencies such as cmake, flatc, and zlib from pinned source/binary downloads.

Important APIs/types/functions: creates temp dir, detects architecture, downloads cmake if missing with arch-specific checksum, builds/installs flatbuffers `flatc` if missing, then downloads/builds/installs zlib 1.2.12 with checksum verification.

Control flow: enter tempdir, conditionally install cmake, conditionally install flatc, always install zlib, then popd.

State and persistence: writes to `/usr/local` via installers and `sudo make install`; downloads/builds under a temp dir and removes archives/build dirs.

Dependencies/integration points: requires wget, sha256sum, tar, cmake/make/compiler toolchain, sudo, network access, and Linux arch names matching upstream artifacts.

Risks: zlib URL under `zlib.net/fossils` and pinned checksums can go stale. The variable `zmake_actual_shasum` appears typo-named but is used consistently. Always installing zlib can overwrite system libraries. Tempdir is not removed at the end.

Test signals: no direct tests; build/check-flatc workflows reveal missing dependencies.
