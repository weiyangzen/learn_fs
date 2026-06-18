# sources/distributed-fs/ceph-client/drivers/platform/raspberrypi/vchiq-mmal/Kconfig

Purpose: Kconfig option for the BCM2835 MMAL service over VCHIQ.

Important APIs, types, and functions: `config BCM2835_VCHIQ_MMAL` is a tristate depending on `BCM2835_VCHIQ`. Its help states that it enables the MMAL API over VCHIQ for VideoCore multimedia services.

Control flow: selected by configuration; the parent Raspberry Pi Kconfig sources this file under the VideoCore menu.

State and persistence: configuration state persists in `.config`; no runtime state.

Dependencies and integration points: depends on the VCHIQ core driver and integrates with the `vchiq-mmal/Makefile` to build `bcm2835-mmal-vchiq.o`.

Risks: help text contains a minor typo ("Broadcomd"). Enabling this without consumers still builds the MMAL VCHIQ service object; disabling it removes MMAL kernel support even if camera/multimedia drivers expect it.

Test signals: build with `BCM2835_VCHIQ_MMAL=y/m/n` and confirm object inclusion and symbol availability for MMAL consumers.
