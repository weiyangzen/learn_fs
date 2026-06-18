## sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/lib.sh

Purpose: small netfilter-local shell library that imports the parent networking selftest library and adds a command availability helper.

Important APIs: sets `net_netfilter_dir` from the resolved script path, sources `../lib.sh`, and defines `checktool()`.

Control flow: `checktool <command> <message>` executes the command with stdout/stderr suppressed; if it fails, it prints a kselftest skip message and exits with `$ksft_skip`. This centralizes common dependency checks used by many netfilter scripts.

State and persistence: no persistent state beyond shell variables/functions. Dependencies are Bash, `readlink -e`, and the parent `../lib.sh` defining `ksft_skip` and namespace helpers. Risks include unsafe command-string evaluation (`$1` is executed by shell word splitting), but all callers pass fixed command strings. Test signal is immediate skip when required tools are missing.
