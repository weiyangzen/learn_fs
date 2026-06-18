# sources/distributed-fs/ipfs-kubo/test/3nodetest/data/Dockerfile

Purpose: builds a data-only container image for the three-node integration test.

Important APIs and control flow: starts from Ubuntu, adds generated `filetiny` and `filerand` into `/data`, and declares `/data` as a volume.

State and persistence: seeds the shared Docker volume with test input files.

Dependencies and integration: used by `fig.yml` as the data service, with server and client using `volumes_from`.

Risks and test signals: assumes Makefile has generated the data files before image build. No direct tests.
