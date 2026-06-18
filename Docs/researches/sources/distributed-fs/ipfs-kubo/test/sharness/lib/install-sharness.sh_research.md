## sources/distributed-fs/ipfs-kubo/test/sharness/lib/install-sharness.sh

Purpose: installs the vendored/expected sharness framework into `test/sharness/lib/sharness` when required.

Important APIs and control flow: the script sets strict shell behavior, computes directories, defines `die`, verifies prerequisites, fetches or prepares sharness assets, and creates the local `sharness.sh`/library layout consumed by `test-lib.sh`. State is written under `test/sharness/lib/sharness`.

Dependencies and integration points: depends on POSIX shell utilities and the sharness source location configured by the script. It integrates with `Rules.mk` through the `$(SHARNESS_$(d))` dependency.

Risks: network or upstream layout assumptions can break bootstrapping if sharness is not already present. Because the test framework is sourced by every shell test, a partial install creates broad failures. Test signal is the presence of sourceable `lib/sharness/sharness.sh` and `lib-sharness`.
