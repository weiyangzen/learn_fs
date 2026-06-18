# sources/distributed-fs/ceph-client/drivers/pinctrl/cirrus/pinctrl-cs47l90.c

Purpose: CS47L90/CS47L91 group table for the shared Madera pinctrl driver.

Important APIs/types/functions: defines MIF1-3, AIF1-4, DMIC3-5, and `pdmspk1` groups, exported as `cs47l90_pin_chip` with `CS47L90_NUM_GPIOS`.

Control flow: selected by Madera core for parent types `CS47L90` and `CS47L91`.

State and persistence: descriptor constants only.

Dependencies/integration: Madera MFD headers and `pinctrl-madera.h`.

Risks: CS47L90 differs from CS47L85 in DMIC and speaker coverage; copying tables across codecs can expose invalid groups. Hidden config must be selected by the parent MFD option.

Test signals: compile with CS47L90 support, verify debugfs group list lacks DMIC6 and PDM speaker 2, and exercise MIF/AIF/DMIC mux states.
