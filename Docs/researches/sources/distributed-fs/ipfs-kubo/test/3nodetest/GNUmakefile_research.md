# sources/distributed-fs/ipfs-kubo/test/3nodetest/GNUmakefile

Purpose: orchestrates the legacy three-node Docker integration test.

Important APIs and control flow: `test` runs `clean` and `setup`, then `run-test-on-img.sh`. `setup` builds the IPFS image and creates tiny/random data files. `docker_ipfs_image` builds an image from the root Dockerfile. `clean` stops/removes fig services, deletes generated binaries/data/build outputs, and removes dangling Docker images.

State and persistence: creates `data/filetiny`, `data/filerand`, `bin/random`, Docker images/containers, and build logs/profiling outputs.

Dependencies and integration: relies on Docker, legacy `fig`, repository test random binary, and sibling scripts.

Risks and test signals: cleanup uses broad Docker commands that can remove exited containers and dangling images beyond the test. Uses old `fig` tooling and old Docker tag syntax in scripts. No automated unit tests for Makefile behavior.
