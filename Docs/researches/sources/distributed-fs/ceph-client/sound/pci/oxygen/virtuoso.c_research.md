
# sources/distributed-fs/ceph-client/sound/pci/oxygen/virtuoso.c

Purpose: PCI module entry for Asus Xonar Virtuoso cards, delegating board identification to PCM179x, CS43xx, and WM87x6 model providers.

Important functions/data: `xonar_ids` lists Asus subsystem IDs plus broken-EEPROM fallback. `get_xonar_model` tries `get_xonar_pcm179x_model`, then `get_xonar_cs43xx_model`, then `get_xonar_wm87x6_model`. `xonar_probe` handles ALSA module slot arrays and calls shared `oxygen_pci_probe`. Driver uses shared PM and shutdown.

Control flow/state: no board private state here; it selects the model provider, then `oxygen_lib.c` allocates model_data and initializes the selected board.

Dependencies: `xonar.h`, shared Oxygen core, and linked board objects from Makefile. Risks include provider ordering, duplicate subsystem IDs, and broken EEPROM fallback selecting the wrong model. Test signals: probe every listed Xonar ID, broken EEPROM matching, module parameter enable/index behavior, PM, shutdown cleanup, and ensuring all provider objects link.
