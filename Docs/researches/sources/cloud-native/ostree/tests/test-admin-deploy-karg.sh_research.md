# sources/cloud-native/ostree/tests/test-admin-deploy-karg.sh

Purpose: validates deployment-time kernel argument propagation, proc-cmdline import, and duplicate handling.

Important APIs/functions: `setup_os_repository`, `pull-local`, repeated `ostree admin deploy --karg=...`, `--karg-proc-cmdline`, and regex assertions against BLS `options` lines.

Control flow: deploys with base `root` and `quiet`, redeploys with additional kargs, checks they are carried forward into later deployments, imports current `/proc/cmdline`, and verifies filtered/expected arguments in loader entries.

State/persistence: updates `sysroot/boot/loader/entries/ostree-*.conf` and deployment metadata. Dependencies include host `/proc/cmdline`, so some assertions account for filtered bootloader-managed args.

Integration/risk/test signals: protects karg inheritance semantics used by admin deploy and upgrade. Risks are host cmdline variability and exact options ordering. Five TAP cases report karg scenarios.
