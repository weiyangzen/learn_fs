# sources/control-plane/rook/images/image.mk

Purpose: shared image build and cache framework for Rook image Makefiles.

Important APIs/types/functions: forces `GOOS=linux`, maps `GOARCH` to platform arch, handles `CACHEBUST`, verbosity, `PULL`, `IMAGE_OUTPUT_DIR`, targets `build`, `clean`, `prune`, `clean.images`, `clean.build`, `cache.lookup`, `cache.images`, `cache.prune`, and `debug.nuke`.

Control flow: image-specific makefiles implement `do.build`; this file wraps builds with cache tagging, cleanup, and pruning. Cache tags use UTC timestamps and an MRU-like retention policy.

State and persistence: local container image cache under repository `cache/`, build registry images, and optional output directories.

Dependencies/integration: depends on common make library, Docker/Podman command variables, GNU utilities, and platform env.

Risks: cleanup/prune/delete targets remove local images and containers; cache date comparison depends on tag format.

Test signals: dry-run or isolated Docker environment for `cache.images`, `cache.prune PRUNE_DRYRUN=1`, and unknown GOARCH failure.
