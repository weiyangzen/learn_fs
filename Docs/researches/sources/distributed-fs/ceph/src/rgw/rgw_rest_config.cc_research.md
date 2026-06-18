# sources/distributed-fs/ceph/src/rgw/rgw_rest_config.cc

## Purpose

`rgw_rest_config.cc` implements the admin REST endpoint that returns RGW zone configuration. It is a small handler used by authenticated admin clients that call the config resource with `type=zone`.

## Important APIs and Functions

`RGWOp_ZoneConfig_Get::send_response()` fetches `RGWZoneParams` from the RADOS-backed zone service and serializes it as JSON under `zone_params`. `RGWHandler_Config::op_get()` dispatches GET requests to `RGWOp_ZoneConfig_Get` only when the query argument `type` equals `zone`.

## Control Flow

The REST manager creates an `RGWHandler_Config`. For GET, the handler inspects `s->info.args`. A zone request constructs `RGWOp_ZoneConfig_Get`; any other type returns `nullptr` and lets higher-level REST dispatch handle the unsupported operation. The operation's `execute()` is empty because the data is already available through the driver/service layer; response generation performs the actual fetch and formatter output.

## State and Persistence Behavior

The endpoint is read-only. It does not mutate zone state. It reads zone params from `static_cast<rgw::sal::RadosStore*>(driver)->svc()->zone->get_zone_params()`, so it assumes the configured driver is the RADOS store implementation.

## Dependencies and Integration Points

The file depends on `rgw_rest_config.h`, `rgw_rest_s3.h`, `driver/rados/rgw_sal_rados.h`, and `services/svc_zone.h`. It integrates with admin auth through `RGWHandler_Auth_S3` and requires the `zone=read` capability declared in the header.

## Risks and Test Signals

The explicit RADOS-store cast is a portability risk for alternate SAL drivers. A useful test should call the authenticated config endpoint with `type=zone`, verify a 200 response containing `zone_params`, verify missing or different `type` does not dispatch this op, and verify users without `zone` read caps are rejected.
