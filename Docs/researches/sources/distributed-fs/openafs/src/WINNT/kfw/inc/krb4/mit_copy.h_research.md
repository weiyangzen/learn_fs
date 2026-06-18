## sources/distributed-fs/openafs/src/WINNT/kfw/inc/krb4/mit_copy.h

Purpose: Carries the MIT Kerberos IV copyright, export-control notice, warranty disclaimer, and permission text.

Important APIs/types/functions: No code declarations. It is included by `krb4/des.h` to keep license terms with DES/Kerberos IV API use.

Control flow: None.

State and persistence: None in runtime terms. The licensing notice is source-tree metadata that should persist with redistributed headers.

Dependencies and integration points: Integrated through legacy MIT Kerberos headers and relevant redistribution documentation.

Risks: Removing or altering the notice can violate redistribution expectations. The export-control language is historical but relevant to provenance reviews.

Test signals: Static packaging checks should ensure the notice remains included with K4 DES/Kerberos headers and survives generated SDK packaging.
