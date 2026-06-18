# sources/distributed-fs/ceph-client/tools/testing/selftests/net/can/config

Purpose: this three-line kselftest config declares the kernel features needed by the CAN raw socket tests. It requests `CONFIG_CAN`, `CONFIG_CAN_DEV`, and `CONFIG_CAN_VCAN` as modules.

Important integration points: the selftest framework can use this file to determine required kernel configuration before running the test. `CONFIG_CAN` enables the CAN protocol stack, `CONFIG_CAN_DEV` supplies CAN network device support, and `CONFIG_CAN_VCAN` enables the virtual CAN device used by the default shell wrapper.

State and persistence: the file is declarative only. It does not mutate test state; it describes build/runtime prerequisites.

Risks and test signals: missing `vcan` support causes the wrapper's default `ip link add name vcan0 type vcan` path to skip or fail. A passing environment has the CAN stack and vcan module available, or an externally supplied physical CAN interface that satisfies the wrapper.
