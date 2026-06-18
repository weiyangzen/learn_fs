# sources/distributed-fs/ceph-client/tools/testing/selftests/media_tests/open_loop_test.sh

Purpose: repeatedly invokes `media_device_open` for `/dev/mediaN`.

Important APIs/types/functions: constructs `file=/dev/media$1`, increments a loop counter, captures `./media_device_open -d $file` output, and prints it.

Control flow: infinite loop with no sleep, intended for manual stress during bind/unbind tests.

State and persistence: repeatedly opens and closes media devices through subprocesses.

Dependencies and integration points: built `media_device_open` in current directory, device number argument, root if the C tool enforces it.

Risks: unbounded loop can spam logs/terminal and consume CPU. No exit condition or argument validation.

Test signals: diagnostic loop output; kernel stability under concurrent device churn is the target.
