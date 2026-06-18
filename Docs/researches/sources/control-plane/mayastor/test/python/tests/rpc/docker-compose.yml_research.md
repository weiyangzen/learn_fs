# sources/control-plane/mayastor/test/python/tests/rpc/docker-compose.yml

Purpose: docker-compose fixture for RPC timeout and reactor interrupt-mode smoke tests. It launches one service named `ms1` at `10.1.0.3`, unlike most single-node files that use `ms0`.

Important configuration: command runs io-engine with `${MS1_CORES:-3,4}` and `/tmp/ms1.sock`. Environment exposes ANA/reservation knobs, optional `ENABLE_INTERRUPT_MODE`, optional `NVME_IOQ_POLL_PERIOD`, `RUST_LOG`, PATH, and ASAN settings. Standard mounts and capabilities support SPDK and host temp file access.

State and integration: RPC timeout tests create `/var/tmp/pool1.img`; the compose mount includes `/var/tmp`. Interrupt tests inspect logs and Docker CPU stats for this container, so the fixed name `ms1` is part of the contract.

Risks and test signals: interrupt tests only run when `ENABLE_INTERRUPT_MODE=true`. CPU checks depend on Docker stats availability and host noise. The service must be named `ms1` for Python fixtures and log pattern checks to work.
