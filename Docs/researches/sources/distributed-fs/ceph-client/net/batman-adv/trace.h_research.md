# sources/distributed-fs/ceph-client/net/batman-adv/trace.h

## Purpose
Defines batman-adv trace events, currently a `batadv_dbg` tracepoint that mirrors formatted batman-adv debug messages into the kernel tracing subsystem. It also provides no-op inline trace functions when batman-adv tracing is disabled.

## Important APIs And Types
Defines `TRACE_SYSTEM batadv` and `TRACE_EVENT(batadv_dbg, TP_PROTO(struct batadv_priv *bat_priv, struct va_format *vaf), ...)`. The event records mesh device name, driver/module name, and the formatted debug message through tracepoint string/vstring fields. It sets `TRACE_INCLUDE_PATH .` and `TRACE_INCLUDE_FILE trace` before including `<trace/define_trace.h>`.

## Control Flow
With `CONFIG_BATMAN_ADV_TRACING`, Linux trace macros generate event declarations or definitions depending on whether `CREATE_TRACE_POINTS` is set. Without tracing, the header overrides `TRACE_EVENT` to emit static inline dummy `trace_<name>` functions, allowing call sites to compile without runtime tracing.

## State And Persistence
No batman-adv state is persisted. Enabled trace events write formatted records to kernel tracing buffers managed outside this module.

## Dependencies And Integration Points
Includes `main.h`, netdevice, percpu, printk, and tracepoint headers. It is included by logging code and by `trace.c` for tracepoint instantiation. The event reads `bat_priv->mesh_iface->name`, so call sites must provide a valid mesh interface.

## Risks
Formatted trace strings depend on `va_format` lifetime and valid `bat_priv->mesh_iface`. Trace header guard and `TRACE_HEADER_MULTI_READ` handling must follow kernel tracing rules. The disabled-tracing macro override must stay compatible with trace macro call syntax.

## Test Signals
Builds with tracing enabled and disabled are required. Runtime tests can enable the `batadv:batadv_dbg` event, trigger batman-adv debug logs, and verify device/driver/message fields appear.
