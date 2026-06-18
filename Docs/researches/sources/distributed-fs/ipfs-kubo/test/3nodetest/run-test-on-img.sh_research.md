# sources/distributed-fs/ipfs-kubo/test/3nodetest/run-test-on-img.sh

Purpose: runs the 3nodetest stack against a supplied Docker image reference.

Important APIs and control flow: validates one argument, finds the image ID with `docker images | grep`, tags it as `zaqwsx_ipfs-test-img`, runs `fig build --no-cache`, runs `fig up --no-color` while teeing `build/fig.log`, saves logs and profiling data best-effort, then greps the log tail for `exited with code 0` as success detection.

State and persistence: mutates Docker image tags, builds containers/images, writes `build/fig.log`, logs, and profiling data.

Dependencies and integration: called by the Makefile `test` target; depends on Docker, fig, make, and fixed service behavior.

Risks and test signals: image lookup by grep can match multiple images. Success detection via tail/grep is brittle because fig may not return service exit codes. Old `docker tag -f` syntax may fail on modern Docker.
