# sources/cloud-native/ostree/tests/test-admin-deploy-nomerge.sh

Purpose: verifies `ostree admin deploy --no-merge` creates a fresh deployment without carrying forward mutable `/etc` changes or prior kernel args.

Important APIs/functions: `setup_os_repository`, `pull-local`, `ostree admin deploy`, `admin --print-current-dir`, and assertions on deployment files and BLS options.

Control flow: deploys with `root=LABEL=foo` and `testkarg=1`, writes a local file under `/etc`, redeploys with `--no-merge` and a different root karg, then checks the deployment changed, the local test file is gone, and old kargs are not present.

State/persistence: mutates deployment `/etc` and bootloader entries. Dependencies are syslinux admin setup.

Integration/risk/test signals: guards the explicit opt-out from deployment merging. Risk is narrow single-file coverage. One TAP case reports `no merge deployment`.
