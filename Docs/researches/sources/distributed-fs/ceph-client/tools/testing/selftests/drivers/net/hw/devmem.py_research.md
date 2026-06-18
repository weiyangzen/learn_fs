# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/devmem.py

Purpose: Python kselftest wrapper for `ncdevmem`, validating TCP device-memory RX/TX and HDS payload-size behavior.

Important APIs/functions: `require_devmem()`, `check_rx()`, `check_tx()`, `check_tx_chunks()`, `check_rx_hds()`, `NetDrvEpEnv`, `ksft_disruptive`, `bkg`, `cmd`, `rand_port`, `wait_port_listen`, `socat`, and `ksft_eq`.

Control flow: `require_devmem()` probes `ncdevmem -f IFACE`. RX test runs `ncdevmem` listening locally and sends a known byte stream from the remote via socat. TX tests run remote socat listener and pipe local text through `ncdevmem`, with and without chunking. HDS test iterates payload sizes from 1 byte to 8192 bytes and verifies `ncdevmem` receive success with `-L` fail-on-linear.

State and persistence: Starts background helpers and uses remote deployment. It relies on `ncdevmem` to mutate NIC devmem binding, queues, RSS, and HDS state.

Dependencies and integration points: Requires `ncdevmem` binary, devmem TCP support, udmabuf, remote endpoint, socat, and disruptive test permissions.

Risks and test signals: Failures identify device memory RX/TX, zerocopy send, header split, queue binding, or chunking regressions.
