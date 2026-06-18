<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_many_serverrooms_with_endangered_chunks_priority.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_many_serverrooms_with_endangered_chunks_priority.sh

Purpose: verifies that endangered-chunk read priority keeps files readable when two of three labeled server rooms are stopped under a custom three-server-room goal.

Important APIs, functions, and commands: uses `setup_local_empty_lizardfs`, `lizardfs_chunkserver_daemon`, `file-generate`, `file-validate`, `assert_success`, `lizardfs {setgoal}`; drives configuration through `USE_RAMDISK`, `CHUNKSERVERS`, `CHUNKSERVER_LABELS`, `MASTER_CUSTOM_GOALS`, `MOUNT_EXTRA_CONFIG`, `ENDANGERED_CHUNKS_PRIORITY`, `FILE_SIZE`.

Control flow: The script proceeds through these visible steps: `setup_local_empty_lizardfs info`; `mkdir "${info[mount0]}/dir"`; `lizardfs setgoal three_serverrooms "${info[mount0]}/dir"`; `FILE_SIZE="$size" assert_success file-generate "${info[mount0]}/dir/file_$size"`; `assert_success lizardfs_chunkserver_daemon "$csid" stop &`; `assert_success file-validate "${info[mount0]}/dir/file_"*`.

State and persistence behavior: State and persistence under test include chunk files and replica/part placement, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `USE_RAMDISK`, `CHUNKSERVERS`, `CHUNKSERVER_LABELS`, `MASTER_CUSTOM_GOALS`, `MOUNT_EXTRA_CONFIG`, `ENDANGERED_CHUNKS_PRIORITY`.

Risks and test signals: Risks: main risks are missing prerequisites, daemon readiness races, and assertion coverage that checks counts without validating full contents. Test signals: hard assertions, content validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_many_serverrooms_with_endangered_chunks_priority.sh -->
