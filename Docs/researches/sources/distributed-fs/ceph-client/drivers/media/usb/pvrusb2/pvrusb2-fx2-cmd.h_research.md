<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-fx2-cmd.h -->
# sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-fx2-cmd.h

Purpose: shared FX2 firmware command code definitions for pvrusb2 USB control transactions.

Important APIs/types/functions: defines command bytes for memory/register reads and writes, I2C read/write, USB speed query, streaming on/off, firmware post, Zilog/demod reset pins, power/deep reset, EEPROM address, IR code, and model-specific digital streaming/power commands.

Control flow: hardware, encoder, I2C, IR, firmware, and digital-control code include this header and pass these command values to the lower USB request helper.

State and persistence: no software state. Commands mutate FX2, encoder, I2C, GPIO, power, IR, or digital streaming state in hardware/firmware.

Dependencies and integration: command namespace is shared across pvrusb2 source files and must match FX2 firmware implementations for multiple product generations.

Risks: numeric command drift breaks hardware communication. Some commands exist only on Model 160xxx; using them on other devices requires descriptor gating. Similar analog and DTV streaming commands must not be confused.

Test signals: firmware upload, register/memory access, I2C transfers, analog and DTV stream on/off, IR polling, power/reset commands on supported models.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-fx2-cmd.h -->
