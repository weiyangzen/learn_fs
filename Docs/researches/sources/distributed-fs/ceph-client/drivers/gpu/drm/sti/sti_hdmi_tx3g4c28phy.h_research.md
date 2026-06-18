# sources/distributed-fs/ceph-client/drivers/gpu/drm/sti/sti_hdmi_tx3g4c28phy.h

Purpose: Declares the TX3G4C28 HDMI PHY ops exported to the HDMI controller.

Important API: `extern struct hdmi_phy_ops tx3g4c28phy_ops` supplies the PHY `start` and `stop` callbacks selected by the HDMI OF match table.

Control/state: No state is declared here; the implementation operates on `struct sti_hdmi` provided by the controller.

Dependencies/integration: Includes `sti_hdmi.h` for `struct hdmi_phy_ops` and `struct sti_hdmi`. Used by `sti_hdmi.c` to populate `.data` for `st,stih407-hdmi`.

Risks/test signals: Header and implementation must agree on symbol name and ops lifetime. Build/link coverage catches mismatch.
