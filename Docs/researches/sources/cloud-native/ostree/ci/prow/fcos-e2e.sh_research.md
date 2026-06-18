# sources/cloud-native/ostree/ci/prow/fcos-e2e.sh

Purpose: runs a Fedora CoreOS compose/e2e smoke using the just-built libostree artifacts inside the Prow coreos-assembler image.

Important APIs/functions: environment flags `COSA_SKIP_OVERLAY=1` and `COSA_SUPPRESS_DEPCHECK=1`; commands `ostree --version`, `cosa init`, `rsync`, `cosa fetch`, append to `src/config/image.yaml`, and `cosa build`.

Control flow: create a temporary work directory, initialize FCOS config, copy built component artifacts into `overrides/rootfs`, fetch inputs, force `rootfs: "ext4verity"` to exercise composefs, then build. Kola composefs tests are present but commented out.

State and persistence: creates a temp directory and coreos-assembler build artifacts there; mutates the generated config checkout.

Dependencies and integration: integrates Prow container output `/cosa/component-install`, coreos-assembler, Fedora CoreOS config, and composefs/ext4verity boot content.

Risks and test signals: risks include network fetches, changing FCOS config defaults, disabled kola test execution, and relying on temp storage capacity. Main signal is a successful `cosa build`; uncommented kola tests would improve runtime validation.
