# sources/distributed-fs/ceph-client/drivers/media/mc/Kconfig

Purpose: Kconfig fragment for media-controller-specific options. It currently defines `MEDIA_CONTROLLER_DVB`, an experimental boolean that enables Media Controller API support for DVB.

Important APIs/types/functions: no runtime APIs. The important symbol is `MEDIA_CONTROLLER_DVB`, which depends on `MEDIA_CONTROLLER && DVB_CORE` and is presented as "Enable Media controller for DVB (EXPERIMENTAL)".

Control flow: during kernel configuration, this file contributes one selectable option under the media-controller area. If enabled, downstream DVB code can conditionally compile media-controller integration.

State/persistence: state is the generated kernel configuration symbol in `.config`; no runtime persistence.

Dependencies/integration: sourced by the broader media Kconfig tree. It ties the media-controller core to DVB core availability.

Risks/test signals: since the help text marks DVB media-controller support experimental, build coverage should include both enabled and disabled combinations with `MEDIA_CONTROLLER` and `DVB_CORE`. Defconfig and randconfig coverage can catch unmet dependency or stale symbol use.
