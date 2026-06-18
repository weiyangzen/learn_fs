# sources/cloud-native/ostree/man/ostree-state-overlay@.service.xml

Purpose: documents `ostree-state-overlay@.service`, a systemd unit template for making selected OSTree-committed directories writable with automatically rebased state overlays.

Important APIs/types: man section 8 service page; target path is encoded as the systemd instance name, e.g. `ostree-state-overlay@opt.service` for `/opt`.

Control flow: when instantiated, the service sets up an overlayfs for the target directory. State that modifies OSTree content is deleted during rebase, while other state is kept and merged onto the new base.

State and persistence: creates writable client-side state over immutable content; state persists and is rebased across upgrades but can delete modifications that conflict with OSTree-owned content.

Dependencies and integration: integrates systemd unit templates, overlayfs, OSTree deployment upgrades, `/opt` handling, tmpfiles recommendations, and immutable `/usr` model.

Risks and test signals: risks include weakening immutability for the target, unexpected deletion during rebase, and overusing overlays instead of `/var` symlinks. Signals are systemd enable/start tests, upgrade/rebase overlay tests, and `/opt` writable behavior checks.
