# sources/cloud-native/ostree/tests/test-admin-kargs.sh

Purpose: validates `ostree admin kargs edit-in-place --append-if-missing` for both key/value and bare keyword arguments.

Important APIs/functions: `setup_os_repository`, `pull-local`, `admin deploy`, `admin kargs edit-in-place`, and negative duplicate checks against the loader `options` line.

Control flow: deploys with root and quiet, appends `TESTARG=TESTVALUE` and `ARGWITHOUTKEY`, asserts both appear, then repeats `quiet` and `TESTARG=TESTVALUE` append-if-missing operations and verifies no duplicate trailing entries are created.

State/persistence: mutates the deployment bootloader entry in place. Dependencies are syslinux bootloader layout and command-line parser behavior.

Integration/risk/test signals: protects idempotent karg editing for scripts/tools. Risks are regex limitations for duplicate detection. Two TAP cases cover basic append and duplicate suppression.
