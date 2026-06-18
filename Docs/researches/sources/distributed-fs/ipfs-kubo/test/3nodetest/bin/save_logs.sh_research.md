# sources/distributed-fs/ipfs-kubo/test/3nodetest/bin/save_logs.sh

Purpose: captures Docker logs from the three-node test containers into build artifacts.

Important APIs and control flow: defines a Perl escape-stripping command and pipes logs from bootstrap, client, data, and server containers into `./build/*.log`.

State and persistence: writes log files under `build/`.

Dependencies and integration: invoked by Makefile and `run-test-on-img.sh` after `fig up`; depends on Docker, Perl, and fixed container names.

Risks and test signals: hard-coded names couple it to fig naming. `eval $STRIP` adds shell-evaluation risk, though the string is static. Missing containers fail the corresponding pipeline unless caller ignores errors.
