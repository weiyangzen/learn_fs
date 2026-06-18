<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/trigger/ledtrig-camera.c -->
# sources/distributed-fs/ceph-client/drivers/leds/trigger/ledtrig-camera.c

Purpose: This trigger provides simple global camera flash and torch LED triggers controlled by exported kernel functions.

Important APIs and state: `DEFINE_LED_TRIGGER(ledtrig_flash)` and `DEFINE_LED_TRIGGER(ledtrig_torch)` hold trigger pointers. `ledtrig_flash_ctrl(bool on)` and `ledtrig_torch_ctrl(bool on)` export on/off control and call `led_trigger_event()` with `LED_FULL` or `LED_OFF`.

Control flow: Module init registers simple triggers named `flash` and `torch`; exit unregisters torch then flash. No per-LED activation state is used.

Dependencies and integration: Camera flash/torch drivers can bind LEDs to these trigger names and call the exported GPL control functions.

Risks and test signals: There is no locking beyond LED trigger core behavior. Test module load/unload, exported controls with no LED attached, and both trigger names appearing in LED trigger lists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/trigger/ledtrig-camera.c -->
