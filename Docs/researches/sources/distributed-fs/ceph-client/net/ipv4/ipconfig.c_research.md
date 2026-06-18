# sources/distributed-fs/ceph-client/net/ipv4/ipconfig.c

## Purpose
Implements early boot IPv4 autoconfiguration for systems that need networking before userspace, especially NFS/CIFS root. It parses `ip=`, `nfsaddrs=`, `dhcpclass=`, and `carrier_timeout=` kernel parameters; opens candidate devices; obtains configuration via static parameters, DHCP, BOOTP, or RARP; applies interface address/netmask/broadcast/MTU and default route; records DNS/NTP/root-server data; and exposes boot configuration in proc files.

## APIs, Types, and Functions
Externally visible boot data includes `ic_set_manually`, `ic_proto_enabled`, `ic_myaddr`, `ic_gateway`, `ic_servaddr`, `root_server_addr`, and `root_server_path`; `root_nfs_parse_addr()` is exported for init-time root parsing. Major functions include `ic_open_devs()`, `ic_close_devs()`, `ic_setup_if()`, `ic_setup_routes()`, `ic_defaults()`, RARP handlers `ic_rarp_init()`, `ic_rarp_recv()`, `ic_rarp_send_if()`, BOOTP/DHCP handlers `ic_bootp_init()`, `ic_bootp_send_if()`, `ic_do_bootp_ext()`, `ic_bootp_recv()`, dynamic loop `ic_dynamic()`, proc helpers, `wait_for_devices()`, dispatcher `ip_auto_config()`, parser `ic_proto_name()`, and setup handlers registered with `__setup()`.

## Control Flow
Command-line parsing runs early and sets manual/static/dynamic choices. `ip_auto_config()` runs as a `late_initcall`: it initializes proc output, returns if disabled, waits for devices and deferred probes, opens loopback plus eligible non-loopback devices, waits for carrier, and decides whether dynamic discovery is needed because address/server data is missing or multiple devices are present. Dynamic discovery registers packet handlers, sends DHCP/BOOTP/RARP requests over capable devices with backoff, waits for `ic_got_reply`, handles DHCP offer-to-request-to-ack sequencing, and cleans packet handlers.

When data is available, it parses root server address from `root_server_path`, fills defaults such as hostname and classful netmask, records the protocol used, logs the chosen configuration, sets interface address/netmask/broadcast and optional MTU through devinet/netdevice ioctls, adds a default route if configured, and closes unselected devices except lower devices of the chosen stacked interface.

## State and Persistence
Most control variables are `__initdata` and disappear after init, including open device list, selected device pointer, protocol choices, DHCP identifiers, carrier timeout, receive lock, and reply flags. Persistent boot results include IP address, gateway, server/root addresses/path, nameservers, NTP servers, DNS domain, hostname/domainname updates, configured interface state, route table entries, and proc files `/proc/net/pnp` and `/proc/net/ipconfig/ntp_servers`. Dynamic packet reception is synchronized by `ic_recv_lock`.

## Dependencies and Integration
Integrates with early kernel init, root NFS/CIFS selection, netdevice registration/probing, RTNL, devinet ioctl address configuration, route ioctl, ARP/RARP packet type hooks, handcrafted BOOTP/DHCP packets sent through `dev_queue_xmit()`, procfs/seq_file, UTS namespace names, random transaction IDs, jiffies timers, and build-time protocol options `CONFIG_IP_PNP_DHCP`, `CONFIG_IP_PNP_BOOTP`, and `CONFIG_IP_PNP_RARP`.

## Risks
Risks include boot hangs or long delays waiting for carrier/devices, DHCP option parsing bounds and malformed replies, reliance on init_net only, fragmented BOOTP replies being unsupported, classful netmask guesses, static globals shared across retry loops, fallback DNS overwrite rules, device reopen behavior for root filesystems, proc creation before successful config, and command-line parsing ambiguity for empty fields or client identifiers.

## Test Signals
Validation can use QEMU or network namespaces with early userspace/rootfs simulations for static `ip=`, DHCP, BOOTP, RARP, multiple interfaces, no carrier, missing devices, NFS/CIFS retry-forever paths, root path server-prefix parsing, DHCP options for DNS/domain/root path/MTU/NTP/vendor/client ID, malformed replies, and proc output. Boot logs should confirm selected device, protocol, address, route, nameservers, NTP servers, and cleanup of nonselected devices.
