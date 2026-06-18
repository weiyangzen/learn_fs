# sources/control-plane/external-snapshotter/pkg/webhook/framework.go

Purpose: generic Kubernetes CRD conversion webhook framework for decoding `ConversionReview` requests, invoking a conversion function, and encoding the response with negotiated media type.

Important APIs/types/functions: `convertFunc`, `statusErrorWithMessage`, `statusSucceed`, `doConversionV1`, `serve`, `mediaType`, package `scheme`, `addToScheme`, `serializers`, `getInputSerializer`, and `getOutputSerializer`.

Control flow: `serve` reads the request body, chooses a serializer from `Content-Type`, decodes the object, only accepts apiextensions/v1 `ConversionReview`, calls `doConversionV1`, clears the request in the response, negotiates output from `Accept`, and encodes JSON/YAML. `doConversionV1` unmarshals each raw object to `unstructured.Unstructured`, calls the converter with the desired API version, sets converted APIVersion, and accumulates raw extensions.

State and persistence: stateless per request; no persistent storage. The runtime scheme and serializer map are package-level singletons.

Dependencies and integration: based on Kubernetes agnhost conversion webhook sample; integrates apiextensions v1/v1beta1 schemes, runtime serializers, HTTP, goautoneg, klog, and `convertGroupSnapshotCRD`.

Risks and test signals: risks include accepting only exact media type strings without parameters, potential nil request dereference for malformed `ConversionReview`, logging full request bodies, and no direct v1beta1 request handling despite v1beta1 being in the scheme. Conversion unit tests bypass this layer; webhook cert test only hits server startup/cert reload.
