# File Research: sources/cow-pools/nilfs-utils/Makefile.am

Top-level Automake entry for nilfs-utils. It sets `ACLOCAL_AMFLAGS = -I m4`, descends into `lib bin sbin include man etc scripts`, distributes `autogen.sh`, and includes `.gitignore` entries in `EXTRA_DIST`.

This file defines the project’s build traversal order: libraries first, then user binaries, privileged/system binaries, headers, documentation, configuration, and scripts.
