# sources/distributed-fs/ceph-client/include/uapi/linux/virtio_bt.h

Purpose: defines the virtio Bluetooth device feature and configuration ABI.

Important APIs/types/functions: feature bits identify vendor HCI support, Microsoft vendor support, AOSP vendor support, and the v2 config layout. Enums define primary config type and vendor IDs for none, Zephyr, Intel, and Realtek. `virtio_bt_config` carries type, vendor, and Microsoft opcode in a packed legacy layout; `virtio_bt_config_v2` adds an alignment byte and uses a naturally aligned layout.

Control flow: the guest negotiates virtio feature bits, selects the config layout based on `VIRTIO_BT_F_CONFIG_V2`, reads type/vendor/opcode, and configures the Bluetooth HCI transport accordingly. Vendor extension support gates use of vendor-specific commands.

State and persistence: config-space fields are static descriptive state. Runtime HCI command/event state is outside this header.

Dependencies and integration: includes `linux/virtio_types.h` and integrates with virtio transport, guest Bluetooth HCI stacks, and VMM/device implementations that emulate Bluetooth controllers.

Risks: using the wrong config layout can misread `vendor` and `msft_opcode`. Vendor extension bits should be treated as capability gates. The legacy struct is packed, so cross-language implementations need exact byte layout.

Test signals: config layout tests with and without `CONFIG_V2`, vendor feature negotiation tests, HCI bring-up smoke tests, and ABI compile checks.
