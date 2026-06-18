# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/lib/py/__init__.py

Purpose: Re-export layer that makes shared `tools/testing/selftests/net/lib/py` helpers available to hardware driver tests through a local `lib.py` import path.

Important APIs/types: `KSFT_DIR`, `sys.path.append`, and re-exported classes/functions including `NetNS`, `NetdevSimDev`, `EthtoolFamily`, `NetdevFamily`, `DevlinkFamily`, `NlError`, `CmdExitFailure`, `bkg`, `cmd`, `defer`, `ethtool`, `ip`, BPF helpers, `KsftSkipEx`, `KsftFailEx`, `KsftXfailEx`, `ksft_run`, `ksft_exit`, `ksft_variants`, and environment classes.

Control flow: On import, it computes the kselftest root, appends it to `sys.path`, and imports selected helpers one by one from `net.lib.py` to avoid lint false positives.

State and persistence: Mutates Python process import path only.

Dependencies and integration points: Central integration point for most Python files in `drivers/net/hw`, allowing local relative imports while sharing common framework code.

Risks and test signals: Path calculation must remain correct relative to this file. Import failures break most hardware Python tests.
