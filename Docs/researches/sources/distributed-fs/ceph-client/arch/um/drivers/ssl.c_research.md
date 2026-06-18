<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/ssl.c -->
# sources/distributed-fs/ceph-client/arch/um/drivers/ssl.c

Purpose: implements UML virtual serial lines (`ttyS*`) using the common line/channel framework.

Important APIs/types/functions: `NR_PORTS` is 64. Static state includes `opts`, `driver`, `conf[]`, `def_conf`, `serial_lines[]`, and `ssl_init_done`. Functions include `ssl_config()`, `ssl_get_config()`, `ssl_remove()`, `ssl_install()`, `ssl_console_write()`, `ssl_console_device()`, `ssl_console_setup()`, `ssl_init()`, `ssl_exit()`, `ssl_chan_setup()`, and `ssl_non_raw_setup()`.

Control flow: boot-time `ssl...` setup records per-line or default channel strings. Late init registers a TTY serial driver, updates xterm titles with UMID, configures all 64 lines from command/default strings, and registers a `ttyS` console. TTY operations delegate to `line.c`; mconsole config/remove/query use the embedded `mc_device`.

State and persistence: per-line runtime state lives in `serial_lines[]`; boot command strings persist as pointers in `conf[]`/`def_conf`. No host data is persisted.

Dependencies and integration points: depends on TTY, console, channel/line framework, mconsole, UML setup/help macros, and default `CONFIG_SSL_CHAN`.

Risks: all 64 lines are configured at init, so invalid defaults can produce repeated errors. `ssl-non-raw` changes global channel options before line setup. Console registration depends on line setup success.

Test signals: boot with `ssl0=pty`, `ssl=tty:/dev/...`, `ssl-non-raw`, use `/dev/ttyS*`, mconsole `config sslN=...`, remove/query serial lines, and serial console output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/ssl.c -->
