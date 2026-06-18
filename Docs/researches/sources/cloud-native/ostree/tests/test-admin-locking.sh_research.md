# sources/cloud-native/ostree/tests/test-admin-locking.sh

Purpose: stress-tests admin deployment locking by running many concurrent retained deploys.

Important APIs/functions: `setup_os_repository`, GNU `parallel`, `getconf _NPROCESSORS_ONLN`, `ostree admin deploy --retain`, `admin status`, and line-count assertions.

Control flow: skips if GNU parallel is unavailable, pulls and deploys a base runtime, computes twice the online CPU count, launches that many parallel deploy commands, then checks `ostree admin status` contains the expected number of matching deployments.

State/persistence: concurrently writes sysroot deployments, bootloader entries, repo refs, and lock-protected admin state. Dependencies include GNU parallel and sufficient filesystem capacity.

Integration/risk/test signals: catches races in admin lock acquisition and deployment list mutation. Risks include slow/flaky behavior under high CPU counts and exact status counting. One TAP case reports `deploy locking`.
