# File Research: sources/block-storage/bcache-tools/make-bcache.c

This standalone command wrapper includes `make-bcache.h` and calls `make_bcache(argc, argv)`. The real formatting implementation lives in `make.c`, allowing both `make-bcache` and the multi-command `bcache make` path to share code.
