# sources/control-plane/mayastor/scripts/reclaim-space.sh

Purpose: frees root filesystem space by running Nix and Docker garbage collection when available space is below a requested threshold.

Important APIs/types/functions: expects first argument `MIN_FREE_GIB`, defines `get_avail_gib` using `df --output=avail /`, runs `nix-collect-garbage` and `docker image prune --force --all`.

Control flow: prints current free GiB, exits early if above threshold, otherwise enables shell tracing for cleanup commands and prints free space afterward.

State/persistence: deletes unreferenced Nix store paths and all unused Docker images.

Dependencies/integration: CI maintenance helper for disk pressure before large builds/tests.

Risks: `$1` is read under `set -e` without default, so calling with no argument fails. Docker prune all can remove useful cached images and slow subsequent jobs.

Test signals: output free-space number should increase or meet the requested threshold.
