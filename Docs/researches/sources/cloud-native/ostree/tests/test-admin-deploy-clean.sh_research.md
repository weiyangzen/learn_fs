# sources/cloud-native/ostree/tests/test-admin-deploy-clean.sh

Purpose: confirms undeploying the only deployment removes generated deployment refs from the sysroot repository.

Important APIs/functions: `setup_os_repository`, `pull-local`, `ostree admin deploy`, `ostree admin undeploy`, `ostree refs`, and negative content assertions.

Control flow: initializes a syslinux sysroot, pulls and deploys a runtime, undeploys index `0`, lists refs in `sysroot/ostree/repo`, and verifies no `ostree/` deployment refs remain.

State/persistence: writes then removes deployment state and bootloader artifacts; validates repository refs after cleanup. It depends on admin harness initialization and deployment-ref naming.

Integration/risk/test signals: catches leaks in generated deployment refs, which would affect pruning and status reporting. Risk is limited coverage of multiple-deployment cleanup. One TAP plan entry reports `deploy + undeploy repo prune`.
