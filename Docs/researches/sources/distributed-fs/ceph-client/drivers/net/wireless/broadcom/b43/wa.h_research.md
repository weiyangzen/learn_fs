# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/wa.h

Purpose: Declares the public PHY workaround entry points for the b43 driver.

Important APIs and types: Declares `b43_wa_initgains(struct b43_wldev *dev)` for gain initialization and `b43_wa_all(struct b43_wldev *dev)` for the full workaround sequence. Uses a conventional include guard and relies on surrounding b43 headers for the `struct b43_wldev` declaration.

Control flow encoded by the header: The header only exposes the two phases. Callers choose between gain-only setup and the complete workaround set implemented in `wa.c`.

State and persistence: No state is stored here. The declared functions write persistent hardware register/table state through the implementation.

Dependencies and integration points: Included by `wa.c` and G-PHY initialization code. It is a narrow interface boundary between PHY bring-up code and the workaround implementation.

Risks: The header does not document PHY-type restrictions; `b43_wa_all` currently only supports G-PHY in the implementation and warns for other PHY types. Callers must ensure the device is in a state where PHY/radio/table writes are valid.

Test signals: Compile tests catch prototype drift. Runtime tests should verify callers invoke these functions only for supported PHY paths and that unsupported PHY types do not rely on side effects beyond warning behavior.
