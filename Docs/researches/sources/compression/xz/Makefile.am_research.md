# sources/compression/xz/Makefile.am

## Purpose
This Automake top-level file controls distribution content, documentation packaging, man-page conversion, release tarball generation, and top-level subdirectory traversal for the autotools build.

## Important Targets and Variables
It sets `GZIP_ENV=-9n`, `DIST_SUBDIRS`, conditional `SUBDIRS`, documentation and example install lists, `EXTRA_DIST`, `ACLOCAL_AMFLAGS`, and `manfiles`. `dist-hook` generates `ChangeLog`, converts man pages to ASCII text via `build-aux/manconv.sh`, and runs `license-check.sh`. `mydist` validates the liblzma map, updates translations, optionally derives a snapshot version from `git describe`, runs license checks, and creates a sorted owner-normalized gzip dist. `pdf-local` creates A4 and letter PDFs from man pages.

## State, Dependencies, and Integration
It depends on Automake conditionals such as `COND_GNULIB` and `COND_DOC`, `git`, `groff`, `po4a`, Make recursion, and build-aux scripts. Generated state includes distribution directories, `ChangeLog`, text/PDF man pages, and tarballs.

## Risks and Test Signals
This file is central to release reproducibility and packaging completeness. Risks include missing tools silently skipping some artifacts, stale translation generation, and license-check failures late in packaging. The `mydist` target is a strong release gate because it runs validation before `dist-gzip`.
