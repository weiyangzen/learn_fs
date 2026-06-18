# sources/distributed-fs/ceph-client/include/media/drv-intf/sh_vou.h

Purpose: Platform-data interface for SuperH Video Output Unit boards.

Important APIs/types/functions: Bus polarity flags describe pixel clock, HSYNC, and VSYNC polarity. `enum sh_vou_bus_fmt` selects 8-bit, 16-bit, or BT.656 bus. `sh_vou_pdata` carries bus format, I2C adapter ID, encoder board info, and flags.

Control flow: Platform code supplies output encoder and bus wiring; the SH VOU driver configures output timing and creates/uses the I2C subdevice.

State and persistence: Static platform configuration only; runtime output state is in the VOU driver and connected subdevice.

Dependencies and integration: Depends on I2C board info and integrates SuperH VOU with external encoders.

Risks and test signals: Risks are bus-width and sync-polarity mismatches or missing encoder board data. Test each bus mode, sync polarity flags, I2C subdevice probe, and active video output timing.
